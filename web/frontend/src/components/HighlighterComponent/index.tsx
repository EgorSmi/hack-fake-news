import React from "react";

interface HighLighterInterface {
    text: string
    pattern: string
    color: string
}

export const HighLighterComponent = (
    {
        text,
        pattern,
        color
    }: HighLighterInterface): JSX.Element => {

    function render(): JSX.Element {
        const splitted = pattern.split('<h>');

        return (
            <span>
            {splitted.map((s, i) =>
                (i % 2 === 1) ?
                    (<span key={i} style={{backgroundColor: color}}>{s}</span>)
                    : (<span key={i}>{s}</span>)
            )}
        </span>
        )
    }

    return render()
}